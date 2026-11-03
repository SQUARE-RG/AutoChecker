typedef int BinaryFn(int, int);

int main()
{
    BinaryFn* fn = nullptr;
    return fn == nullptr ? 0 : 1;
}
