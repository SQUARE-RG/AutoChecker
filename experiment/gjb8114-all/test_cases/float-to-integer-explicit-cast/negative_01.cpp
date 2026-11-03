int main()
{
    float ratio = 1.85f;
    int count = ratio; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-1]
    return count;
}
