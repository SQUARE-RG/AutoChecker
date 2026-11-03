#define DEREF(p) (*p) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-7]

int main()
{
    int arr[3] = {1, 2, 3};
    int *base = arr;
    int value = DEREF(base + 1);
    return value;
}
