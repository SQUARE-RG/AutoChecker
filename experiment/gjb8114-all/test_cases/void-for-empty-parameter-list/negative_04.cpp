template <typename T>
T defaultValue() { return T{}; } // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-23]

int main(void)
{
    int value = defaultValue<int>();
    return value == 0 ? 0 : 1;
}
