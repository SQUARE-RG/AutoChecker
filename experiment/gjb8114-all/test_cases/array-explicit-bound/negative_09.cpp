int main()
{
    auto sum = [](int value) {
        int arr[]{value, value + 1, value + 2}; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-18]
        return arr[0] + arr[1] + arr[2];
    };
    return sum(1) - 6;
}
