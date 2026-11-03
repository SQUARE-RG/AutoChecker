void cleanup()
{
}

void finish()
{
    return cleanup();
}

int main()
{
    finish();
    return 0;
}
