void negative_08(int x) {
    if (x > 0) {
        if constexpr (true) {
            if (x > 1) {
                if constexpr (true) {
                    if (x > 2) {
                        if constexpr (true) {
                            if (x > 3) {
                                if constexpr (true) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-4-1]
                                    x += 1;
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
