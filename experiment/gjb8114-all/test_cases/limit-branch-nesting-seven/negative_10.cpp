int nested_switch_init_negative(int a, int b, int c, int d, int e, int f, int g, int h) {
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
                                switch (int v8 = h; v8) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-4-1]
                                default:
                                    result = v1 + v2 + v3 + v4 + v5 + v6 + v7 + v8;
                                }
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
    return nested_switch_init_negative(1, 2, 3, 4, 5, 6, 7, 8) == 36 ? 0 : 1;
}
