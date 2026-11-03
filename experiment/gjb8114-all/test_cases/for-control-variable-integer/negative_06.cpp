int main()
{
    for (auto ratio = 0.0; ratio < 1.0; ratio += 0.2) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-9-2]
    {
    }
    return 0;
}
