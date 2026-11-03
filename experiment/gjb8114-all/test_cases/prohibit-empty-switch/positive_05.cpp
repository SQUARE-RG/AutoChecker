enum class Mode
{
    idle,
    active
};

int state_value(Mode mode)
{
    int result = 0;
    switch (mode)
    {
    case Mode::idle:
    case Mode::active:
        result = 1;
        break;
    }
    return result;
}

int main()
{
    return state_value(Mode::active);
}
