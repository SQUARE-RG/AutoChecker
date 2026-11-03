int main()
{
    volatile unsigned int v = 2;
    unsigned int n = v;
    unsigned int* p = new unsigned int[n + n];
    delete[] p;
    return 0;
}
