enum Flags
{
    None,
    Readable = 1 << 0, // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-11-4]
    Writable,
    Executable
};

int main()
{
    Flags selected = Writable;
    return static_cast<int>(selected);
}
