constexpr int buffer_size = 4;
int buffer[buffer_size] = {1, 2, 3, 4};

int at(int buffer) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-2]
{
    return buffer >= 0 && buffer < buffer_size ? ::buffer[buffer] : -1;
}

int main()
{
    return at(2);
}
