UPDATE django_site SET domain = 'dev.monthlytetris.info:8000', name = 'dev.monthlytetris.info:8000' WHERE id = 1;
UPDATE classic_tetris_project_twitchchannel SET connected = false;
UPDATE classic_tetris_project_page SET content = regexp_replace(content, 'http(s)?://ctm\.gg', 'http://dev.monthlytetris.info:8000', 'g');
UPDATE classic_tetris_project_page SET content = regexp_replace(content, 'http(s)?://go\.ctm\.gg', 'http://dev.monthlytetris.info:8000', 'g');
UPDATE classic_tetris_project_tournament SET google_sheets_id = NULL, google_sheets_range = NULL;
