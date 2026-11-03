int main()
{
    int* value; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-7]
    value = new int(42);
    int observed = *value;
    delete value;
    return observed == 42 ? 0 : 1;
}
