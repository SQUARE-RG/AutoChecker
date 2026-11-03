using DoublePtr = int**;

int main()
{
    int* value = nullptr;
    DoublePtr pp = &value;
    (void)pp;
    return 0;
}
