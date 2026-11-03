typedef int TData;

int apply(int value)
{
    auto worker = [](TData TData) { return TData + 1; }; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-6]
    return worker(value);
}

int main()
{
    return apply(1);
}
