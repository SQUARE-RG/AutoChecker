int main() {
    int arr[3] = {10, 20, 30};
    int *p = arr;
    p = p + 1;  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-3-3]
    return *p;
}
