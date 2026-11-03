int main()
{
    int sum = 0;
    for (float f = 0.0f; f < 5.0f; f++) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-9-2]
    {
        sum += static_cast<int>(f);
    }
    return 0;
}
