def Post_Form_Match_Case(input: str) -> list[str,str]:
    
    """ takes a unnamed form from a post request on the dashboard and preps the responce so backend can direct to the correct item (video/article/user) etc."""
    
    check = "("
    itemID: str | None = None
    
    print(input)

    if check in input:
        input = input.split("(")
        action = str(input[0])
        itemID = input[1].replace("(","").replace(")","")
    else:
        action = str(input)

    match_case = [action, itemID]

    return match_case