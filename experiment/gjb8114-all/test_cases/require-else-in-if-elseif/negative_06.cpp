int main()
{
    int result = 0;
    auto classify = [&result](int value) -> void
    {
        if (value == 0) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-1]
        {
            result = 1;
        }
        else if (value == 1)
        {
            result = 2;
        }
    };
    classify(2);
    return result;
}
