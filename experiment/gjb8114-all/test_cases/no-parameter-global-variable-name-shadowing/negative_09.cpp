int value = 0;

template <typename T>
T transform(T value) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-2]
{
    return value;
}

int main()
{
    value = 3;
    int result = transform(value);
    return result;
}
