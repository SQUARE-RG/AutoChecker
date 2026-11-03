class sample
{
public:
    static constexpr int values[] = {0, 1, 2}; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-18]
};

int main()
{
    int sum = 0;
    for (int i = 0; i < 3; ++i)
    {
        sum += sample::values[i];
    }
    return sum;
}
