int main()
{
    int* value = nullptr;
    value = new int(42);
    int observed = *value;
    delete value;
    return observed == 42 ? 0 : 1;
}
