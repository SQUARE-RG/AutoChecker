int main() {
    const int arr[3] = {1, 2, 3};
    int (&ref)[3] = const_cast<int (&)[3]>(arr); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-5-2]
    (void)ref;
    return 0;
}
