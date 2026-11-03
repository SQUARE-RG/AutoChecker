constexpr int firstFlag = 0;

enum Flags
{
    None = firstFlag,
    Readable,
    Writable,
    Executable
};

int main()
{
    Flags selected = Writable;
    return static_cast<int>(selected);
}
