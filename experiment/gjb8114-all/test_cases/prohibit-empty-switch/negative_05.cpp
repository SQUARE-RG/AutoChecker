template <typename T>
void inspect(T value)
{
    switch (value) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-3]
    {
    }
}

int main()
{
    inspect(static_cast<short>(1));
    return 0;
}
