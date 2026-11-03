void positive_08(int x) {
    if (x > 0) {
        if constexpr (true) {
            if (x > 1) {
                if constexpr (true) {
                    if (x > 2) {
                        if constexpr (true) {
                            if (x > 3) {
                                x += 1;
                            }
                        }
                    }
                }
            }
        }
    }
}
