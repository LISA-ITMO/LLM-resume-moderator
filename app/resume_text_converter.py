from schemas import ResumeToGovernment, LanguageLevel, SoftwareSkillLevel


def is_empty_value(value) -> bool:
    """Проверяет, является ли значение пустым (None, пустая строка, пустой список)"""
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    if isinstance(value, list) and len(value) == 0:
        return True
    return False

def resume_to_text(resume: ResumeToGovernment) -> str:
    """Преобразует резюме в форматированный текст для LLM с учетом пустых полей"""
    
    sections = []
    
    # Основная информация
    main_info = []
    
    if not is_empty_value(resume.fullname):
        main_info.append(f"ФИО: {resume.fullname}")
    if not is_empty_value(resume.citizenship):
        main_info.append(f"Гражданство: {resume.citizenship}")
    if not is_empty_value(resume.passportOrEquivalent):
        main_info.append(f"Паспорт: {resume.passportOrEquivalent}")
    if not is_empty_value(resume.snils):
        main_info.append(f"СНИЛС: {resume.snils}")
    if not is_empty_value(resume.birthdate):
        main_info.append(f"Дата рождения: {resume.birthdate}")
    if not is_empty_value(resume.placeOfBirth):
        main_info.append(f"Место рождения: {resume.placeOfBirth}")
    if not is_empty_value(resume.registrationAddress):
        main_info.append(f"Адрес регистрации: {resume.registrationAddress}")
    if not is_empty_value(resume.actualResidenceAddress):
        main_info.append(f"Адрес проживания: {resume.actualResidenceAddress}")
    if not is_empty_value(resume.contactInformation):
        main_info.append(f"Контактная информация: {resume.contactInformation}")
    if not is_empty_value(resume.fullnameChange):
        main_info.append(f"Смена ФИО: {resume.fullnameChange}")
    
    if main_info:
        sections.append("ОСНОВНАЯ ИНФОРМАЦИЯ\n" + "\n".join(main_info))
    
    # Близкие родственники
    if not is_empty_value(resume.closeRelatives):
        relatives_section = ["БЛИЗКИЕ РОДСТВЕННИКИ"]
        for i, relative in enumerate(resume.closeRelatives, 1):
            relative_info = []
            
            if not is_empty_value(relative.relationship):
                relative_info.append(f"Степень родства: {relative.relationship}")
            if not is_empty_value(relative.fullname):
                relative_info.append(f"ФИО: {relative.fullname}")
            if not is_empty_value(relative.birthdate):
                relative_info.append(f"Дата рождения: {relative.birthdate}")
            if not is_empty_value(relative.job):
                relative_info.append(f"Место работы: {relative.job}")
            if not is_empty_value(relative.address):
                relative_info.append(f"Адрес: {relative.address}")
            
            if relative_info:
                relatives_section.append(f"{i}. " + "\n   ".join([relative_info[0]] + [f"   {line}" for line in relative_info[1:]]))
        
        if len(relatives_section) > 1:  # Если есть хотя бы один родственник с информацией
            sections.append("\n".join(relatives_section))
    
    # Образование
    education_sections = []
    
    # Высшее образование
    if not is_empty_value(resume.education.higherEducation):
        higher_ed = ["ВЫСШЕЕ ОБРАЗОВАНИЕ"]
        for i, edu in enumerate(resume.education.higherEducation, 1):
            edu_info = []
            
            if not is_empty_value(edu.institutionName):
                edu_info.append(f"Учебное заведение: {edu.institutionName}")
            if not is_empty_value(edu.specialty):
                edu_info.append(f"Специальность: {edu.specialty}")
            if not is_empty_value(edu.level):
                edu_info.append(f"Уровень: {edu.level}")
            if not is_empty_value(edu.formOfEducation):
                edu_info.append(f"Форма обучения: {edu.formOfEducation}")
            if not is_empty_value(edu.year):
                edu_info.append(f"Год обучения: {edu.year}")
            if not is_empty_value(edu.haveDiploma):
                edu_info.append(f"Наличие диплома: {'Да' if edu.haveDiploma else 'Нет'}")
            if not is_empty_value(edu.dateOfAdmission) and not is_empty_value(edu.dateOfGraduation):
                edu_info.append(f"Период: {edu.dateOfAdmission} - {edu.dateOfGraduation}")
            elif not is_empty_value(edu.dateOfAdmission):
                edu_info.append(f"Дата поступления: {edu.dateOfAdmission}")
            elif not is_empty_value(edu.dateOfGraduation):
                edu_info.append(f"Дата окончания: {edu.dateOfGraduation}")
            
            if edu_info:
                higher_ed.append(f"{i}. " + "\n   ".join(edu_info))
        
        if len(higher_ed) > 1:
            education_sections.extend(higher_ed)
    
    # Дополнительное образование
    if not is_empty_value(resume.education.additionalEducation):
        additional_ed = ["ДОПОЛНИТЕЛЬНОЕ ОБРАЗОВАНИЕ"]
        for i, edu in enumerate(resume.education.additionalEducation, 1):
            edu_info = []
            
            if not is_empty_value(edu.institutionName):
                edu_info.append(f"Учебное заведение: {edu.institutionName}")
            if not is_empty_value(edu.educationalProgram):
                edu_info.append(f"Программа: {edu.educationalProgram}")
            if not is_empty_value(edu.programType):
                edu_info.append(f"Вид программы: {edu.programType}")
            if not is_empty_value(edu.hoursИumber):
                edu_info.append(f"Количество часов: {edu.hoursИumber}")
            if not is_empty_value(edu.dateOfAdmission) and not is_empty_value(edu.dateOfGraduation):
                edu_info.append(f"Период: {edu.dateOfAdmission} - {edu.dateOfGraduation}")
            elif not is_empty_value(edu.dateOfAdmission):
                edu_info.append(f"Дата поступления: {edu.dateOfAdmission}")
            elif not is_empty_value(edu.dateOfGraduation):
                edu_info.append(f"Дата окончания: {edu.dateOfGraduation}")
            
            if edu_info:
                additional_ed.append(f"{i}. " + "\n   ".join(edu_info))
        
        if len(additional_ed) > 1:
            education_sections.extend(additional_ed)
    
    # Послевузовское образование
    if not is_empty_value(resume.education.postgraduate):
        postgraduate_ed = ["ПОСЛЕВУЗОВСКОЕ ОБРАЗОВАНИЕ"]
        for i, edu in enumerate(resume.education.postgraduate, 1):
            edu_info = []
            
            if not is_empty_value(edu.institutionName):
                edu_info.append(f"Учебное заведение: {edu.institutionName}")
            if not is_empty_value(edu.specialty):
                edu_info.append(f"Специальность: {edu.specialty}")
            if not is_empty_value(edu.degree):
                edu_info.append(f"Ученая степень: {edu.degree}")
            if not is_empty_value(edu.scienceBranch):
                edu_info.append(f"Отрасль наук: {edu.scienceBranch}")
            if not is_empty_value(edu.dateOfAdmission) and not is_empty_value(edu.dateOfGraduation):
                edu_info.append(f"Период: {edu.dateOfAdmission} - {edu.dateOfGraduation}")
            elif not is_empty_value(edu.dateOfAdmission):
                edu_info.append(f"Дата поступления: {edu.dateOfAdmission}")
            elif not is_empty_value(edu.dateOfGraduation):
                edu_info.append(f"Дата окончания: {edu.dateOfGraduation}")
            
            if edu_info:
                postgraduate_ed.append(f"{i}. " + "\n   ".join(edu_info))
        
        if len(postgraduate_ed) > 1:
            education_sections.extend(postgraduate_ed)
    
    if education_sections:
        sections.append("ОБРАЗОВАНИЕ\n" + "\n".join(education_sections))
    
    # Языки
    if not is_empty_value(resume.languges):
        languages_section = ["ВЛАДЕНИЕ ЯЗЫКАМИ"]
        for lang in resume.languges:
            if not is_empty_value(lang.name) and not is_empty_value(lang.level):
                level_map = {
                    LanguageLevel.NATIVE: "Родной",
                    LanguageLevel.SPEAK_FLUENTLY: "Свободно владею",
                    LanguageLevel.CAN_READ_AND_EXPLAIN: "Читаю и могу объяснить",
                    LanguageLevel.READ_TRANSLATE_WITH_DICT: "Читаю и перевожу со словарем"
                }
                level_text = level_map.get(lang.level, lang.level.value)
                languages_section.append(f"- {lang.name}: {level_text}")
        
        if len(languages_section) > 1:
            sections.append("\n".join(languages_section))
    
    # Компьютерные навыки
    if not is_empty_value(resume.softwareSkills):
        skills_section = ["НАВЫКИ РАБОТЫ С КОМПЬЮТЕРОМ"]
        for skill in resume.softwareSkills:
            skill_info = []
            
            if not is_empty_value(skill.type):
                skill_info.append(skill.type)
            if not is_empty_value(skill.nameOfProduct):
                if skill_info:
                    skill_info[-1] += f": {skill.nameOfProduct}"
                else:
                    skill_info.append(skill.nameOfProduct)
            
            if skill_info and not is_empty_value(skill.level):
                level_map = {
                    SoftwareSkillLevel.FLUENT: "Свободно",
                    SoftwareSkillLevel.HAVE_GENERAL_IDEA: "Общее представление",
                    SoftwareSkillLevel.HAVE_NOT_SKILL: "Не владею"
                }
                level_text = level_map.get(skill.level, skill.level.value)
                skills_section.append(f"- {' '.join(skill_info)} ({level_text})")
        
        if len(skills_section) > 1:
            sections.append("\n".join(skills_section))
    
    # Публикации
    if not is_empty_value(resume.publications):
        publications_section = ["НАУЧНЫЕ ТРУДЫ И ПУБЛИКАЦИИ"]
        valid_publications = [pub for pub in resume.publications if not is_empty_value(pub)]
        
        for i, pub in enumerate(valid_publications, 1):
            publications_section.append(f"{i}. {pub}")
        
        if len(publications_section) > 1:
            sections.append("\n".join(publications_section))
    
    # Награды
    if not is_empty_value(resume.awards):
        awards_section = ["ПРЕМИИ И НАГРАДЫ"]
        valid_awards = [award for award in resume.awards if not is_empty_value(award)]
        
        for i, award in enumerate(valid_awards, 1):
            awards_section.append(f"{i}. {award}")
        
        if len(awards_section) > 1:
            sections.append("\n".join(awards_section))
    
    # Военная служба
    military_info = []
    if not is_empty_value(resume.militaryLiable):
        military_info.append(f"Военнообязанный: {'Да' if resume.militaryLiable else 'Нет'}")
    if not is_empty_value(resume.militaryСategory):
        military_info.append(f"Годность: {resume.militaryСategory}")
    
    if military_info:
        sections.append("ВОИНСКАЯ ОБЯЗАННОСТЬ\n" + "\n".join(military_info))
    
    # Дополнительная информация
    additional_info_sections = []
    
    if not is_empty_value(resume.professionalInterests):
        additional_info_sections.append(f"Сфера профессиональных интересов: {resume.professionalInterests}")
    if not is_empty_value(resume.additionalInfo):
        additional_info_sections.append(f"О себе: {resume.additionalInfo}")
    if not is_empty_value(resume.motivation):
        additional_info_sections.append(f"Мотивация: {resume.motivation}")
    if not is_empty_value(resume.source):
        additional_info_sections.append(f"Источник информации о резерве: {resume.source}")
    
    if additional_info_sections:
        sections.append("ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ\n" + "\n".join(additional_info_sections))
    
    return "\n\n".join(sections)