struct Mailbox
{
    struct Formatter { Formatter() = default; int format(int value) const { return value + 1; } } formatter;
    int id;
};

int main()
{
    Mailbox box;
    box.id = 7;
    int result = box.formatter.format(box.id);
    return result == 8 ? 0 : 1;
}
