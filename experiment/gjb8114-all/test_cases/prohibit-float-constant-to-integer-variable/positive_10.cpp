int main()
{
    int* p = new int(8);
    int result = *p;
    delete p;
    return result;
}
