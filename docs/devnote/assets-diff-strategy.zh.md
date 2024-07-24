# 如何比较文件/文件夹是否相同

## 文件比较

比较文件的哈希值.

## 文件夹比较

我们的基本原则是 "乐观对比". 即对于两个陌生的文件夹, 我们优先假设它们是相同的, 并尽可能快地证明它们就是相同的.

需要补充一点注意事项, 我们的乐观对比, 是带有一点 "盲目" 情绪的, 在尽可能快地证明过程中, 我们会为了追求快而大幅忽略结果的严谨性和稳定性. 目前来说, 针对我们的实际使用场景, 这种做法暂时没有遇到问题.

基于该原则, 我们首先对比两个文件夹的修改时间. 如果相同, 则直接予以通过.

如果修改时间不对, 就要深入比较这两个文件夹中的内容. 具体如下:

- 对于子文件夹, 先对比名称是否一致. 然后对比里面的文件 (见下一条).
- 对于子文件, 只对比文件名称和文件体积 (byte) 是否一致.

以上两条规则, 递归进行, 直到完整地遍历两棵文件树.

## 应用

关联代码:

- `depsland.manifest.manifest.T.AssetsInfo`
- `depsland.manifest.manifest.T.Experiments0`
- `depsland.manifest.manifest.Manifest.init`
- `depsland.manifest.manifest.Manifest.load_from_file`
- `depsland.manifest.manifest.Manifest._update_assets.generate_hash`
- `depsland.manifest.manifest._diff_assets.is_same`

## 其他说明事项

- 递归遍历文件夹时, 忽略 `__pycache__`, `.gitkeep`, `.DS_Store` 等常见的可忽略类型. 具体忽略规则见 `lk_utils.filesniff.finder.default_filter`.
