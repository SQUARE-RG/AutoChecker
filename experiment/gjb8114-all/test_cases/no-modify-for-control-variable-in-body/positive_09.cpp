int main()
{
    int total = 0;
    int aux = 8;
    for (int i = 0; i < 8; i++)
    {
        aux >>= 1;
        total += aux;
    }
    return total;
}
