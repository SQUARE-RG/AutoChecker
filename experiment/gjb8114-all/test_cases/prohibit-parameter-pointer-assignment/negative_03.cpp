void assign_pointer_parameter(int* target, int* source)
{
    target = source; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-3]
}

int main()
{
    int first = 1;
    int second = 2;
    assign_pointer_parameter(&first, &second);
    return 0;
}
