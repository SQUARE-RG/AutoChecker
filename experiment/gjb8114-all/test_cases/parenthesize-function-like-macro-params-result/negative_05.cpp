#define IN_RANGE(value, low, high) ((value) >= (low) && (value) <= high) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-7]

int main()
{
    int value = 4;
    int low = 1;
    int high = 3;
    int result = IN_RANGE(value, low, high ? high + 1 : low);
    return result;
}
