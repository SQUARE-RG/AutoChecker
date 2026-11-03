struct Mailbox
{
    struct Formatter { Formatter() = default; int format(int value) const { return value + 1; } }; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-9]
    int id;
};

int main()
{
    Mailbox box;
    box.id = 7;
    return 0;
}
