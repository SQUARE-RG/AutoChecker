int main()
{
    int err = 0;

    try
    {
        throw 1;
    }
    catch (int)
    {
        int caught_value = 2;
        err = caught_value;
    }

    return err;
}
