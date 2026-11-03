int counter = 0;

int bump()
{
    {
        counter += 1;
    }
    return counter;
}

int main()
{
    return bump();
}
