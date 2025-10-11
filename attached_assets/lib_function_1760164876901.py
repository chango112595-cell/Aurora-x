
from textwrap import dedent
def render_function(name: str, brief: str):
    if 'factorial' in name:
        code = dedent("""
        def factorial(n: int) -> int:
            if n < 0: raise ValueError("n must be >= 0")
            r = 1
            for i in range(2, n+1): r *= i
            return r
        """)
        tests = dedent("""
        assert factorial(0) == 1
        assert factorial(5) == 120
        """)
        return code, tests
    code = dedent(f"""
    def {name}(*args, **kwargs):
        """{brief or "Auto-generated function."}"""
        raise NotImplementedError("Please refine specification for {name}.")
    """)
    tests = dedent(f"""
    try:
        {name}()
    except NotImplementedError:
        pass
    """)
    return code, tests
