int main()
{
    int target = 0;
    int* ptr = &target;
    float value = -2.5f;
    *ptr = value; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-1]
    return target;
}
