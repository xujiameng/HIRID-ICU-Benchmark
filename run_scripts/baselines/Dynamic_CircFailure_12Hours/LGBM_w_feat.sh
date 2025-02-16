source activate icu-benchmark
python -m icu_benchmarks.run train \
                             -c configs/hirid/Classification/LGBM_w_feat.gin \
                             -l logs/benchmark_exp/LGBM_w_feat/ \
                             -t Dynamic_CircFailure_12Hours\
                             -o True \
                             --depth 3 \
                             --subsample-feat 0.66 \
                             --subsample-data 0.33 \
                             -sd 1111 2222 3333 4444 5555 6666 7777 8888 9999 0000
