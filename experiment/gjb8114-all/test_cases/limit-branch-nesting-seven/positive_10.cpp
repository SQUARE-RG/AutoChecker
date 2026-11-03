int nested_switch_init_positive(int a, int b, int c, int d, int e, int f, int g) {
    int result = 0;
    switch (int v1 = a; v1) {
    default:
        switch (int v2 = b; v2) {
        default:
            switch (int v3 = c; v3) {
            default:
                switch (int v4 = d; v4) {
                default:
                    switch (int v5 = e; v5) {
                    default:
                        switch (int v6 = f; v6) {
                        default:
                            switch (int v7 = g; v7) {
                            default:
                                result = v1 + v2 + v3 + v4 + v5 + v6 + v7;
                            }
                        }
                    }
                }
            }
        }
    }
    return result;
}

int main() {
    return nested_switch_init_positive(1, 2, 3, 4, 5, 6, 7) == 28 ? 0 : 1;
}
