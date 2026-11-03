void qsort(void* base, unsigned long count, unsigned long size, int (*compare)(const void*, const void*)) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-1]
{
    (void)base;
    (void)count;
    (void)size;
    (void)compare;
}

int compare_int(const void* left, const void* right)
{
    int lhs = *static_cast<const int*>(left);
    int rhs = *static_cast<const int*>(right);
    return (lhs > rhs) - (lhs < rhs);
}

int main()
{
    int values[2] = {3, 1};
    qsort(values, 2, sizeof(int), compare_int);
    return 0;
}
