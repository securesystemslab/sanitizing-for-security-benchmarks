# SoK: Sanitizing for Security

## Preparing SPEC CPU2006

* Install SPEC CPU2006 benchmark (see [instructions](https://www.spec.org/cpu2006/docs/install-guide-unix.html))
* Apply [CPU2006.patch](CPU2006.patch)
* Set up environment variables and paths for SPEC

```bash
cd <SPEC INSTALLATION DIR>
. ./shrc
```

## Sanitizers and configurations

| Sanitizer | Configuration | Description |
| --------- | ------------- | ----------- |
| `memcheck` | `baseline-spec` | lvm/clang 6.0.0 |
|            | `spec`          | Valgrind 3.13.0, binaries compiled with llvm/clang 6.0.0 |
| `asan`    | `baseline-spec` | llvm/clang 6.0.0 |
|           | `spec`          | ASan bundled with llvm/clang 6.0.0 |
| `lowfat`  | `baseline-spec` | llvm/clang 4.0.0 |
|           | `spec`          | LowFat [11671b0b](https://github.com/GJDuck/LowFat/commit/11671b0b9b3345cf48ba5e1770a25552cf424cce) |
| `dangsan` | `baseline-spec` | llvm/clang r251286, binutils 2.26.1, gperftools c46eb1f3 + DangSan speedup patch |
|           | `spec`          | DangSan [78006af3](https://github.com/vusec/dangsan/commit/78006af30db70e42df25b7d44352ec717f6b0802) |
| `msan`    | `baseline-spec` | llvm/clang 6.0.0 |
|           | `spec`          | MSan bundled with llvm/clang 6.0.0 |
| `typesan` | `baseline-spec-cpp` | llvm 8f4f26c9, clang d59a142e, compiler-rt 961e7872, gperftools c46eb1f3 |
|           | `spec-cpp`          | TypeSan [fe25d436](https://github.com/vusec/typesan/commit/fe25d436f92faf0b1da6ca43ae9171681b8f7c06) |
| `hextype` | `baseline-spec-cpp` | llvm 8f4f26c9c, clang d59a142e, compiler-rt 961e7872 |
|           | `spec-cpp`          | HexType [64c5469c](https://github.com/HexHive/HexType/commit/64c5469c53bd6b79b404c1b203da8a114107ec96) |
| `cfi`    | `baseline-spec-cpp` | llvm/clang 6.0.0, binutils 2.30 |
|          | `spec-cpp`          | Clang CFI bundled with llvm/clang 6.0.0 |
| `hexvasan` | `baseline-spec` | llvm 4607999, clang c3709e7, compiler-rt 38631af |
|            | `spec`          | HexVASAN [164b16e14](https://github.com/HexHive/HexVASAN/commit/164b16e14bd7524b36f4cc613143e50409bac7d5) |
| `ubsan`   | `baseline-spec` | llvm/clang 6.0.0 |
|           | `spec`          | UBSan bundled with llvm/clang 6.0.0 |


```bash
# List sanitizers
python benchmark.py --help

# List configurations
python benchmark.py <SANITIZER> --help
```

## Building sanitizers

```bash
python benchmark.py <SANITIZER> --setup <CONFIG>
```

## Running benchmarks

```bash
python benchmark.py <SANITIZER> --run <CONFIG>
```

## Citing our work

If you use this benchmarking script in an academic work, please cite our [paper](https://www.computer.org/csdl/proceedings/sp/2019/6660/00/666000a187.pdf):

```
@inproceedings{song2019sanitizing,
  title =	 {{SoK}: Sanitizing for Security},
  author =	 {Song, Dokyung and Lettner, Julian and Rajasekaran, Prabhu
                  and Na, Yeoul and Volckaert, Stijn and Larsen, Per
		  and Franz, Michael},
  booktitle =	 {IEEE Symposium on Security and Privacy},
  year =	 {2019}
}
```
