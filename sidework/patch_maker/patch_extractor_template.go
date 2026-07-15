package main

import (
	"archive/zip"
	"embed"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"
)

//go:embed grocery/assets_map.json
var assetsMapBytes []byte

//go:embed grocery/assets.zip
var assetsZipBytes []byte

func main() {
	patchID := "c32a7f82869746729205e5153065ecbd"

	// extract embed data to local files
	extractedDir := filepath.Join(".", patchID)
	if err := os.RemoveAll(extractedDir); err != nil {
		panic(err)
	}
	if err := os.MkdirAll(extractedDir, 0755); err != nil {
		panic(err)
	}
	if err := os.WriteFile(
		filepath.Join(extractedDir, "assets_map.json"),
		assetsMapBytes, 0644,
	); err != nil {
		panic(err)
	}
	if err := os.WriteFile(
		filepath.Join(extractedDir, "assets.zip"),
		assetsZipBytes, 0644,
	); err != nil {
		panic(err)
	}
	if err := extractZip(
		filepath.Join(extractedDir, "assets.zip"),
		extractedDir,
	); err != nil {
		panic(err)
	}

	backupsDir := filepath.Join(extractedDir, "backups")
	if err := os.MkdirAll(backupsDir, 0755); err != nil {
		panic(err)
	}

	// load assets map
	data, err := os.ReadFile(filepath.Join(extractedDir, "assets_map.json"))
	if err != nil {
		panic(err)
	}

	var assetsMap map[string][]interface{}
	if err := json.Unmarshal(data, &assetsMap); err != nil {
		panic(err)
	}

	// apply patch
	for fileID, v := range assetsMap {
		fileI := filepath.Join(extractedDir, "assets", fileID)
		fileM := filepath.Join(extractedDir, "backups", fileID)
		dstRelpath, _ := v[1].(string)
		appendOrDelete, _ := v[2].(bool)
		fileO := filepath.Join("source", dstRelpath)

		if appendOrDelete { // append/update
			if _, err := os.Stat(fileI); os.IsNotExist(err) {
				panic(fmt.Sprintf("file not found: %s", fileI))
			}
			if _, err := os.Stat(fileO); err == nil { // update
				if err := moveFile(fileO, fileM); err != nil {
					panic(err)
				}
				if err := moveFile(fileI, fileO); err != nil {
					panic(err)
				}
			} else { // append
				if err := moveFile(fileI, fileO); err != nil {
					panic(err)
				}
			}
		} else { // delete
			if err := moveFile(fileO, fileM); err != nil {
				panic(err)
			}
		}
	}

	// generate new manifest
	// TODO: currently not supported
}

func extractZip(zipPath, destDir string) error {
	r, err := zip.OpenReader(zipPath)
	if err != nil {
		return err
	}
	defer r.Close()

	for _, f := range r.File {
		fpath := filepath.Join(destDir, f.Name)

		// check for zip slip vulnerability
		if !strings.HasPrefix(
			fpath, filepath.Clean(destDir)+string(os.PathSeparator),
		) {
			return fmt.Errorf("illegal file path: %s", fpath)
		}

		if f.FileInfo().IsDir() {
			if err := os.MkdirAll(fpath, f.Mode()); err != nil {
				return err
			}
			continue
		}

		if err := os.MkdirAll(filepath.Dir(fpath), 0755); err != nil {
			return err
		}

		outFile, err := os.OpenFile(
			fpath, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, f.Mode(),
		)
		if err != nil {
			return err
		}

		rc, err := f.Open()
		if err != nil {
			outFile.Close()
			return err
		}

		_, err = io.Copy(outFile, rc)
		outFile.Close()
		rc.Close()
		if err != nil {
			return err
		}
	}
	return nil
}

// moveFile moves a file from src to dst. If os.Rename fails (e.g. across
// devices), it falls back to copy-and-remove.
func moveFile(src, dst string) error {
	if err := os.MkdirAll(filepath.Dir(dst), 0755); err != nil {
		return err
	}
	if err := os.Rename(src, dst); err == nil {
		return nil
	}

	// fallback: copy then remove
	in, err := os.Open(src)
	if err != nil {
		return err
	}
	defer in.Close()

	out, err := os.OpenFile(dst, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0644)
	if err != nil {
		return err
	}
	defer out.Close()

	if _, err := io.Copy(out, in); err != nil {
		return err
	}
	if err := out.Close(); err != nil {
		return err
	}
	if err := in.Close(); err != nil {
		return err
	}
	return os.Remove(src)
}
