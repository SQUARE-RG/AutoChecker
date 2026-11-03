int main() {
    int a = 3;
    int b = -3;
    bool equal = false;
    if (a + b == 0) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-5]
    {
        equal = true;
    }
    return equal ? 0 : 1;
}
