// negative_06.cpp
int main() {
    int n = 0;
again:
    n++;
    if (n >= 3) {
        return n;
    }
    goto again;  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-5-1]
    return 0;
}
