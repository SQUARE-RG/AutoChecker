template <typename T>
void negative_06(T value, int a, int b) {
    if constexpr (sizeof(T) > 0) {
        switch (a) {
        case 0:
            if constexpr (sizeof(T) > 1) {
                switch (b) {
                case 1:
                    if constexpr (sizeof(T) > 2) {
                        switch (a + b) {
                        case 2:
                            if constexpr (sizeof(T) > 3) {
                                switch (a - b) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-4-1]
                                case 3:
                                    (void)value;
                                    break;
                                default:
                                    break;
                                }
                            }
                            break;
                        default:
                            break;
                        }
                    }
                    break;
                default:
                    break;
                }
            }
            break;
        default:
            break;
        }
    }
}
