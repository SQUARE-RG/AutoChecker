static int helper(int value) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-13]
{
    return value + 1;
}

int main()
{
    const char* text = "helper";
    return text[0] == 'h' ? 0 : 1;
}
