int nested_if_init_negative(int a, int b, int c, int d, int e, int f, int g, int h) {
    int result = 0;
    if (int v1 = a; v1 > 0) {
        if (int v2 = b; v2 > 0) {
            if (int v3 = c; v3 > 0) {
                if (int v4 = d; v4 > 0) {
                    if (int v5 = e; v5 > 0) {
                        if (int v6 = f; v6 > 0) {
                            if (int v7 = g; v7 > 0) {
                                if (int v8 = h; v8 > 0) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-4-1]
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
    return nested_if_init_negative(1, 2, 3, 4, 5, 6, 7, 8) == 36 ? 0 : 1;
}
