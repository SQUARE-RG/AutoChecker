int main()
{
    unsigned int value = 42u;
    unsigned int result = static_cast<unsigned int>(value) + 1u; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-6]
    return result == 43u ? 0 : 1;
}
