template <typename T>
void positive_06(T value, int a, int b) {
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
                                (void)value;
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
