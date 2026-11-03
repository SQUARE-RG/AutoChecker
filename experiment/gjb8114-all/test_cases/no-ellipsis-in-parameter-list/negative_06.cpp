using VariadicCallback = int (*)(int, ...); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-15]

int main()
{
    VariadicCallback callback = nullptr;
    return callback == nullptr ? 0 : 1;
}
