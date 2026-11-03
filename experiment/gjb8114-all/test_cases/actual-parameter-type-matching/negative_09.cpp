template <typename T>
T consume(T value)
{
    return value;
}

int main()
{
    short small = 7;
    long result = consume<long>(small); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-2]
    return static_cast<int>(result);
}
